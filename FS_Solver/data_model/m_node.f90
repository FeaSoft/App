! Description:
! Definition of a finite element node.
module m_node
    implicit none
    
    private
    public t_node, new_node
    
    type t_node
        real :: coordinates(3) ! nodal coordinates
    end type
    
    interface new_node
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Finite element node constructor.
    type(t_node) function constructor(x, y, z) result(this)
        real, intent(in) :: x, y, z ! nodal coordinates
        this%coordinates = [x, y, z]
    end function
    
end module
