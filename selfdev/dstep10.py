import numpy as np
import traceback
import unittest

class Variable:
    def __init__(self, data):
        if data is not None:
            if not isinstance(data, np.ndarray):
                raise TypeError('{}은(는) 지원하지 않습니다.'.format(type(data)))

        self.data = data # 통상값, 다차원배열(nparray)
        self.grad = None # 미분값, 다차원배열(nparray), None에서 역전파 시 미분값 대입
        self.creator = None
    
    def set_creator(self, func):
        self.creator = func

    # def backward(self):
    #     f = self.creator                    #1. 함수를 가져온다.
    #     if f is not None:
    #         x = f.input                     #2. 함수의 입력을 가져온다.
    #         x.grad = f.backward(self.grad)  #3. 함수의 backward 메서드를 호출 한다.
    #         x.backward()                    # 하나 앞의 변수의 backward 메서드를 호출한다.

    def backward(self):
        '''
        추가
        '''
        if self.grad is None:
            self.grad = np.ones_like(self.data)

        funcs = [self.creator]
        while funcs:
            f = funcs.pop()             #함수를 가져온다.
            x, y = f.input, f.output    #함수의 입력과 출력을 가져온다.
            x.grad = f.backward(y.grad) 

            if x.creator is not None:
                funcs.append(x.creator) #하나 앞의 함수를 리스트에 추가한다.

def as_array(x):
    if np.isscalar(x):
        return np.array(x)
    return x

class Function:
    def __call__(self, input):
        x = input.data
        y = self.forward(x)
        output = Variable(as_array(y))
        output.set_creator(self)
        self.input = input
        self.output = output
        return output
    
    def forward(self, x):
        raise NotImplementedError()

    #미분을 계산하는 역전파   
    def backward(self, gy):
        raise NotImplementedError()

class Square(Function):
    def forward(self, x):
        y = x ** 2
        return y

    def backward(self, gy):
        x = self.input.data
        gx = 2 * x * gy
        return gx


class Exp(Function):
    def forward(self, x):
        y = np.exp(x)
        return y
    
    def backward(self, gy):
        x = self. input.data
        gx = np.exp(x) * gy
        return gx


def square(x):
    f = Square()
    return f(x)

def exp(x):
    return Exp()(x)


def numerical_diff(f, x, eps=1e-4):
    x0 = Variable(x.data - eps)
    x1 = Variable(x.data + eps)
    y0 = f(x0)
    y1 = f(x1)
    return (y1.data - y0.data)/(2*eps)

class SquareTest(unittest.TestCase):
    def test_forward(self):
        x = Variable(np.array(2.0))
        y = square(x)
        expected = np.array(4.0)
        self.assertEqual(y.data, expected)

    def test_backward(self):
        x = Variable(np.array(3.0))
        y = square(x)
        y.backward()
        expected = np.array(6.0)
        self.assertEqual(x.grad, expected)

    # def test_gradient_check(self):
    #     print("-----test_gradient_check")
    #     x = Variable(np.random.rand(1))
    #     y = square(x)
    #     y.backward()
    #     num_grad = numerical_diff(square, x)
    #     #print(num_grad.data)
    #     # print(x.grad)
    #     flg = np.allclose(x.grad, num_grad)
    #     #print(flg)
    #     self.assertTrue(flg)

    def test_gradient_check(self):
        print("-1-")
        x = Variable(np.random.rand(1))
        print(x.data)
        y = square(x)
        y.backward()
        num_grad = numerical_diff(square, x)
        print(num_grad)
        print(x.grad)
        flg = np.allclose(x.grad, num_grad)
        self.assertTrue(flg)


print("-0-")
try:
    # x = Variable(np.array([[0, 0.5 , 1],[1,2,3]]))
    x = Variable(np.random.rand(1))
    print(x.data)
    y = square(exp(square(x)))
    y.backward()
    print(x.grad)
    print("OK")
except Exception as e:    # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
    print('예외가 발생했습니다.', e)
